"""

    Directory.py

    This program is designd to extract data from a Team Unify database and
    reformat it in a way that it can be used to create a printed directory.

    See the file "Directory Process.rtf" for details on the manual extraction
    process.

    Copyright (c) 2017 by the Greenmeadow Community Association

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import csv

# defaults
rowNum = 0	# row of input
kidCount = 0
# Friggin Python doesn't have Java style 'for'??
blocks = ['','','','','','','','','','','','','','','','','','','','','','']
kids = ['','','','','','','','','','','','']
redirects = ['']
redirects[:] = []		# add to this as new redirects are found
redirCount = 0
currAcct = ''
acct1stName = ''
acctLastName = ''
acctPName = ''		# what will be printed in the directory
acctType = ''
acctPType = ''
addr = ''
cityZip = ''
phone = ''
email = ''
blockNum = 0
inDir = False

# Change these as necessary!!
currYear = 2017		# one step below hard-coding
directory = "C://bruces/temp/GM DB/"

gmOut = open('gmOut.txt', mode='w')
with open('customexport.csv') as csvfile:
    rdr = csv.DictReader(csvfile)
    for row in rdr:
        rowNum=rowNum+1	# no friggin increment?!
        if (row['Account Status'] != 'Active') : 	# or row['Member Status'] != 'Active'): 
             continue	# ignore entry if hidden
        # If new account
        if (row['Email'] != currAcct):
            # First save last Acct info (if valid)
            # Actually first convert acctType to shortened value and fix for Greenmeadow Swim Team
            acctPType = 'WHOOPS! ' + acctType	# default - hopefully always overridden
            if (acctType == 'Greenmeadow Swim Team') :
                if (blockNum != 0) : acctPType = 'AS'
                else : acctPType = 'RS'
            elif (acctType == 'Nonmember') : acctPType = 'N'
            elif (acctType == 'Resident Swim') : acctPType = 'RS'
            elif (acctType == 'Associate Swim') : acctPType = 'AS'
            elif (acctType == 'Resident Individual Swim') : acctPType = 'RI'
            elif (acctType == 'Resident Individual') : acctPType = 'RI'
            elif (acctType == 'Associate Individual Swim') : acctPType = 'AI'
            elif (acctType == 'Fair Share') : acctPType = 'F'
            elif (acctType == 'Senior Fair Share') : acctPType = 'SF'
            #else : acctPType = 'WHOOPS! ' + acctType   ????
            if (inDir):
                # Save last acct OwnerNames, Address, Email, Phone, acctType, and child first names & birth mo/yr
                gmOut.write(acctPName + " \t" + addr + " \t" + phone + ' \t'+ acctPType + "\r")
                kidlist = ''
                if (kidCount > 0):
                    for kid in kids: kidlist = kidlist + kid + " "
                    gmOut.write(kidlist + ' \t' + cityZip + ' \t' + email + "\r")
                else : gmOut.write('\t\t\t' + cityZip + ' \t' + email + "\r")
                gmOut.write("\r")	# just a separator line
                if (blockNum != 0):
                    if (kidCount == 0) : 
                        # Save block info (all but email?)
                        blocks[blockNum-1] = blocks[blockNum-1] + addr + ' \t' + acctPName + " \t" + phone + " \t" + acctPType + "\r"
                    else :
                        blocks[blockNum-1] = blocks[blockNum-1] + addr + ' \t' + acctPName + " \t" + phone + " \t" + acctPType + "\r\t\t" + kidlist + '\r'
                #
            else: 
                while redirCount > 0 :		 # gotta be a better way to do this, but...
                    del redirects[-1]
                    redirCount = redirCount-1
            # Default new Acct params
            inDir = False		# default case
            redirCount = 0		# reset to no redirects for new acct
            member = False		# ditto (guilty until proven innocent!)
            kidCount = 0		# reset to no kids for new account
            kids = ['','','','','','','','','','','','']
            currAcct = row['Email']
            acct1stName = row['Acct. First Name'].strip()
            acctLastName = row['Acct. Last Name'].strip()
            acctPName = acctLastName + ", " + acct1stName
            # Get account level params
            addr = row['Address'] 
            cityZip = row['City'] + ' ' + row['Zip']
            phone = row['Home Phone']
            if (row['Email Valid'] == 'Yes'):  email = row['Email']
            else:  email = ' - '
            # get Block Number into blockNum - if it's valid (assuming block# applied to all residents)
            btemp = row['Residents Block Number']
            blockNum = 0		# default
            if (btemp.isdecimal()):
                blkInt = 0
                blkInt = int(btemp)
                if (blkInt>0 and blkInt<23):
                    blockNum = blkInt
                #
            #67
        # For each Member record
        # if any member of acct is valid then acct is valid
        roster = row['Roster Group']
        if roster == '2017 Swim Members (Famliy & Indiv)' or roster == '2017 ALL Fair Share':  member = True
        elif ('2017' in roster): print("Yikes! ", acctPName, roster)
        if (member or (blockNum > 0 and blockNum < 23)):
            # Paid 2017 Account (or local) - so start processing for directory
            inDir = True
            if (member):  acctType = row['Billing Group']
            else:  acctType = 'Nonmember'
        # gather up params
        mem1stName = row['Memb. First Name'].strip()
        memLastName = row['Memb. Last Name'].strip()
        # if dup kid name, ignore
        for kname in kids :
            if (mem1stName in kname): continue
        dob = row['Date Of Birth']
        if (dob == '01/01/2001'):  yearBlank = True
        else: yearBlank = False
        dList = dob.split('/')
        dayOfBirth = dList[1]
        monthOfBirth = dList[0]
        byear = dList[2]
        yob = int(dList[2])
        
        # next determine if spouse with different last name
        # year check is for weird people that give their children blended last names
        if (memLastName.lower() != acctLastName.lower() and (yearBlank or currYear-yob >= 30)):
            #add to redirect list
            redirects.append(memLastName + ', ' + mem1stName + ' -> ' + acctLastName + ', ' + acct1stName)
            redirCount = redirCount+1	# to roll back if account invalid
            # create new acct name as combo of existing parent + other named one
            if not '&' in acct1stName:
                 acctPName = acctPName + " & " + mem1stName + ' ' + memLastName
            elif mem1stName in acctPName :
                 # replace 1st name in acct name with full name of spouse
                 acctPName.replace(mem1stName, mem1stName + ' ' + memLastName)
            else :
                 # append full name to account name and let checkers figure it out
                 acctPName = acctPName + " & " + mem1stName + ' ' + memLastName
        # now check if parent by 1st name match
        elif ((mem1stName.lower() in acct1stName.lower()) and (yearBlank or currYear - yob >= 30)):
            # probably parent, unless child name matches/part of parent and year blank - sigh
            junk = 0		# no action, but that's not allowed in python??
        # else check for kid - almost certainly if yob<30, else (dob blank) guessing
        elif (yearBlank or (currYear - yob) < 30):
            # kid (hopefully) so add to record with birth month/year
            kids[kidCount] = mem1stName + " " + monthOfBirth + '/' + byear
            kidCount = kidCount+1
        # try for case of parent not in acct name
        elif (currYear - yob >= 30) and not '&' in acct1stName:
            # add (hopefully) parent to acctName
            acctPName = acctPName + " & " +mem1stName
        #if (acctLastName == "Brodt") : break	# for testing purposes - short printout
    # end of (input) rows
    gmOut.close()
    with open('blocksOut.txt', mode='w') as blkout:
        for i in range(len(blocks)): blkout.write("Block "+ repr(i+1) + "\r" + blocks[i] + "\r")
    blkout.close()
    with open('redirects.txt', mode='w') as redirOut:
        for i in redirects: 
            redirOut.write(i)
            redirOut.write("\r")
    redirOut.close()
# end of the world
